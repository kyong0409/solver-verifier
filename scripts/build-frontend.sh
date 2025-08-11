#!/bin/bash

# Build React frontend for RFP Analyzer

echo "🚀 Building React frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend" || exit 1

echo "📦 Installing dependencies..."
npm install

# Install additional required dependencies
echo "📦 Installing Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

echo "🔨 Building frontend..."
npm run build

# Check if build was successful
if [ -d "build" ]; then
    echo "✅ Frontend build completed successfully!"
    echo "📂 Built files are in frontend/build/"
    
    # Copy build to parent directory if needed
    if [ ! -d "../frontend-build" ]; then
        cp -r build ../frontend-build
        echo "📋 Copied build to project root as frontend-build/"
    fi
    
    echo ""
    echo "🎉 Ready to serve! Run the FastAPI server:"
    echo "   cd .."
    echo "   uv run uvicorn main:app --reload"
    echo ""
    echo "Then visit: http://localhost:8000"
    
else
    echo "❌ Frontend build failed!"
    exit 1
fi