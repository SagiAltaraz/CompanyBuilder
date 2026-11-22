FROM node:20-alpine
WORKDIR /app

# Install deps first for layer caching.
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest and run the dev server.
COPY . .

EXPOSE 3000
# --host binds to 0.0.0.0 so the container port is reachable from the host.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
