# DcisionAI Manufacturing Optimizer - Web Application

A modern, Perplexity-style web application to showcase the DcisionAI Manufacturing MCP Server with real-time AI-powered optimization.

## Features

- **Modern UI**: Clean, dark-themed interface inspired by Perplexity
- **Real-time Optimization**: Live manufacturing optimization using AI agents
- **Interactive Results**: Detailed breakdown of optimization results
- **Example Queries**: Pre-built examples for different manufacturing scenarios
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │   Flask         │    │   MCP Server    │
│   Frontend      │◄──►│   Backend       │◄──►│   (FastMCP)     │
│   (Port 3000)   │    │   (Port 5000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Node.js 16+ and npm
- Python 3.11+
- MCP Server running on localhost:8000

## Setup Instructions

### 1. Install Dependencies

```bash
# Install React dependencies
npm install

# Install Python backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Start the MCP Server

```bash
# In the main dcisionai-mcp-manufacturing directory
cd ..
source venv/bin/activate
python mcp_server.py
```

### 3. Start the Backend Server

```bash
# In a new terminal, in the web_app directory
cd backend
python app.py
```

### 4. Start the React Frontend

```bash
# In a new terminal, in the web_app directory
npm start
```

## Access the Application

- **Web App**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **MCP Server**: http://localhost:8000

## Usage

1. **Open the web app** in your browser
2. **Check connection status** - should show "Connected" if MCP server is running
3. **Try example queries** or type your own manufacturing optimization problem
4. **View results** - see detailed breakdown of intent classification, data analysis, model building, and optimization solution

## Example Queries

- "Optimize production line efficiency with 50 workers across 3 manufacturing lines"
- "Minimize supply chain costs for 5 warehouses across different regions"
- "Maximize quality control efficiency while reducing inspection costs"
- "Optimize resource allocation for sustainable manufacturing processes"

## Development

### Project Structure

```
web_app/
├── public/
│   └── index.html
├── src/
│   ├── App.js          # Main React component
│   ├── App.css         # Custom styles
│   ├── index.js        # React entry point
│   └── index.css       # Global styles
├── backend/
│   ├── app.py          # Flask backend server
│   └── requirements.txt
├── package.json
├── tailwind.config.js
└── README.md
```

### Key Components

- **App.js**: Main React component with chat interface
- **Backend**: Flask server that proxies requests to MCP server
- **Styling**: Tailwind CSS with custom dark theme
- **Icons**: Lucide React icons for modern UI

## UI Features

- **Dark Theme**: Modern dark interface
- **Real-time Chat**: Perplexity-style conversation interface
- **Status Indicators**: Connection status and loading states
- **Responsive Cards**: Detailed optimization result breakdown
- **Smooth Animations**: Fade-in and typing animations
- **Mobile Friendly**: Responsive design for all devices

## Deployment

### Production Build

```bash
# Build React app for production
npm run build

# The build folder contains the production build
```

### Docker Deployment

```dockerfile
# Dockerfile for production deployment
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### Common Issues

1. **"Disconnected" Status**
   - Make sure MCP server is running on localhost:8000
   - Check if backend server is running on localhost:5000

2. **CORS Errors**
   - Backend server handles CORS automatically
   - Make sure backend is running before frontend

3. **Optimization Timeout**
   - Complex problems may take 30-60 seconds
   - Check MCP server logs for errors

### Debug Mode

```bash
# Run backend in debug mode
cd backend
FLASK_DEBUG=1 python app.py

# Run React in development mode
npm start
```

## Performance

- **Response Time**: 10-30 seconds for typical optimization problems
- **Real-time Updates**: Live status indicators and progress
- **Error Handling**: Graceful error messages and fallbacks
- **Caching**: Browser caching for static assets

## Success Metrics

- **Modern UI**: Perplexity-style interface
- **Real Optimization**: Live AI-powered results
- **Interactive Results**: Detailed breakdown display
- **Responsive Design**: Works on all devices
- **Error Handling**: Graceful error management

---

**Ready to showcase DcisionAI Manufacturing Optimization!**
