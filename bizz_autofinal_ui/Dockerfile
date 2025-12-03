# Dockerfile for the Next.js frontend

# Stage 1: Build the Next.js application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package.json ./package.json
COPY package-lock.json ./package-lock.json

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Next.js application
RUN npm run build

# Stage 2: Serve the Next.js application with a minimal server
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

# Copy Next.js build output
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose the port the app runs on
EXPOSE 3000

# Start the Next.js production server
CMD ["npm", "run", "start"]
