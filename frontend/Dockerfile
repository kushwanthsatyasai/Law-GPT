FROM node:20-alpine

WORKDIR /app
COPY package.json package-lock.json* /app/
RUN npm install --no-audit --no-fund
COPY . /app
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--port", "3000", "--host", "0.0.0.0"]
