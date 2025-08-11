import React, { useState, useRef } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';

interface FileUploaderProps {
  onFilesChange: (files: FileList | null) => void;
  supportedFormats: string[];
  maxFiles?: number;
  disabled?: boolean;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  onFilesChange,
  supportedFormats,
  maxFiles = 10,
  disabled = false
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!supportedFormats.includes(fileExt)) {
      return `${file.name}: Unsupported format. Supported: ${supportedFormats.join(', ')}`;
    }
    
    // 100MB limit
    if (file.size > 100 * 1024 * 1024) {
      return `${file.name}: File too large (max 100MB)`;
    }
    
    return null;
  };

  const handleFiles = (files: FileList | null) => {
    if (!files) return;

    const fileArray = Array.from(files);
    const newErrors: string[] = [];
    const validFiles: File[] = [];

    // Validate each file
    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        newErrors.push(error);
      } else {
        validFiles.push(file);
      }
    });

    // Check total file count
    if (selectedFiles.length + validFiles.length > maxFiles) {
      newErrors.push(`Too many files. Maximum ${maxFiles} files allowed.`);
      setErrors(newErrors);
      return;
    }

    // Update state
    const updatedFiles = [...selectedFiles, ...validFiles];
    setSelectedFiles(updatedFiles);
    setErrors(newErrors);
    
    // Convert to FileList-like structure
    const dataTransfer = new DataTransfer();
    updatedFiles.forEach(file => dataTransfer.items.add(file));
    onFilesChange(dataTransfer.files);
  };

  const removeFile = (index: number) => {
    const updatedFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(updatedFiles);
    
    if (updatedFiles.length === 0) {
      onFilesChange(null);
    } else {
      const dataTransfer = new DataTransfer();
      updatedFiles.forEach(file => dataTransfer.items.add(file));
      onFilesChange(dataTransfer.files);
    }
  };

  const clearAll = () => {
    setSelectedFiles([]);
    setErrors([]);
    onFilesChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    
    if (!disabled) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragOver
            ? 'border-blue-500 bg-blue-50'
            : disabled
            ? 'border-gray-200 bg-gray-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className={`mx-auto mb-4 ${disabled ? 'text-gray-400' : 'text-gray-500'}`} size={48} />
        
        <p className={`mb-2 text-lg font-medium ${disabled ? 'text-gray-400' : 'text-gray-700'}`}>
          {disabled ? 'Processing...' : 'Upload RFP Documents'}
        </p>
        
        <p className={`mb-4 text-sm ${disabled ? 'text-gray-400' : 'text-gray-500'}`}>
          Drag and drop files here, or{' '}
          <button
            type="button"
            className={`font-medium underline ${
              disabled ? 'text-gray-400 cursor-not-allowed' : 'text-blue-600 hover:text-blue-800'
            }`}
            onClick={() => !disabled && fileInputRef.current?.click()}
            disabled={disabled}
          >
            browse
          </button>
        </p>
        
        <p className="text-xs text-gray-400">
          Supported: {supportedFormats.join(', ')} • Max {maxFiles} files • 100MB each
        </p>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={supportedFormats.join(',')}
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
          disabled={disabled}
        />
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="space-y-2">
          {errors.map((error, index) => (
            <div key={index} className="flex items-center space-x-2 text-red-600 text-sm">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          ))}
        </div>
      )}

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-700">
              Selected Files ({selectedFiles.length})
            </h4>
            <button
              type="button"
              onClick={clearAll}
              className="text-sm text-red-600 hover:text-red-800"
              disabled={disabled}
            >
              Clear All
            </button>
          </div>
          
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <File size={20} className="text-gray-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-500"
                    disabled={disabled}
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;