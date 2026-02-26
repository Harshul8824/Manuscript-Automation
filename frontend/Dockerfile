# Dockerfile for React frontend
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Serve with a lightweight HTTP server
FROM node:20-alpine

WORKDIR /app

# Install serve to run the built app
RUN npm install -g serve

# Copy built app from build stage
COPY --from=build /app/dist ./dist

# Expose port
EXPOSE 5173

# Start the application
CMD ["serve", "-s", "dist", "-l", "5173"]
