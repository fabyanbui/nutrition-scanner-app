FROM node:20-alpine

WORKDIR /app

# Copy root package.json for workspaces
COPY package.json package-lock.json* ./
COPY apps/web/package.json apps/web/
COPY packages/shared-types/package.json packages/shared-types/
COPY packages/config/package.json packages/config/

# Install dependencies
RUN npm install

# Copy source
COPY apps/web apps/web/
COPY packages packages/

# Build web
WORKDIR /app/apps/web
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
