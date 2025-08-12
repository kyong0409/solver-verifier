import { useEffect, useRef, useState, useCallback } from 'react';

interface ProgressData {
  total_steps: number;
  current_step: number;
  overall_progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  current_iteration: number;
  max_iterations: number;
  steps: any[];
}

interface WebSocketMessage {
  type: 'progress_update' | 'step_update' | 'error' | 'complete';
  session_id: string;
  timestamp: string;
  data: any;
}

interface UseWebSocketReturn {
  progress: ProgressData | null;
  isConnected: boolean;
  error: string | null;
  finalResult: any;
  connect: (sessionId: string) => void;
  disconnect: () => void;
}

const useWebSocket = (): UseWebSocketReturn => {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finalResult, setFinalResult] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback((sessionId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use backend URL (port 8000) instead of frontend URL (port 3000)
    const backendHost = window.location.hostname + ':8000';
    const wsUrl = `${wsProtocol}//${backendHost}/pipeline/ws/${sessionId}`;
    
    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected:', sessionId);
        setIsConnected(true);
        setError(null);
        
        // Send ping to keep connection alive
        if (wsRef.current) {
          wsRef.current.send('ping');
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          if (event.data === 'pong') {
            return; // Ignore pong responses
          }

          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message:', message);

          switch (message.type) {
            case 'progress_update':
              setProgress(prevProgress => ({
                ...prevProgress,
                ...message.data,
                steps: prevProgress?.steps || []
              }));
              break;

            case 'step_update':
              setProgress(prevProgress => {
                if (!prevProgress) return null;
                
                const stepIndex = prevProgress.steps.findIndex(
                  step => step.step_id === message.data.step_id
                );
                
                if (stepIndex !== -1) {
                  const updatedSteps = [...prevProgress.steps];
                  updatedSteps[stepIndex] = {
                    ...updatedSteps[stepIndex],
                    ...message.data
                  };
                  
                  return {
                    ...prevProgress,
                    steps: updatedSteps
                  };
                }
                
                return prevProgress;
              });
              break;

            case 'error':
              setError(message.data.error || 'Unknown error occurred');
              setProgress(prevProgress => ({
                ...prevProgress!,
                status: 'failed'
              }));
              break;

            case 'complete':
              setFinalResult(message.data);
              setProgress(prevProgress => ({
                ...prevProgress!,
                status: 'completed',
                overall_progress: 100
              }));
              console.log('Pipeline completed:', message.data);
              break;

            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        
        // Try to reconnect after a delay if not manually closed
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect(sessionId);
          }, 3000);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        setError('Connection error occurred');
      };

      // Send periodic pings to keep connection alive
      const pingInterval = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send('ping');
        } else {
          clearInterval(pingInterval);
        }
      }, 30000); // Ping every 30 seconds

      // Clean up interval when component unmounts
      return () => {
        clearInterval(pingInterval);
      };

    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Failed to establish connection');
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    progress,
    isConnected,
    error,
    finalResult,
    connect,
    disconnect
  };
};

export default useWebSocket;