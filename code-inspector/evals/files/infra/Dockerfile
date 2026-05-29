FROM node:latest

WORKDIR /app
COPY . .
RUN npm install

ENV API_KEY=hardcoded-key

CMD ["npm", "start"]
