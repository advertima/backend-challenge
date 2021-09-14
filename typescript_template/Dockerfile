FROM node:16-alpine as builder

WORKDIR /app

COPY package.json yarn.lock /app/
RUN yarn

COPY . .

RUN yarn build

FROM node:16-alpine

WORKDIR /app

COPY package.json yarn.lock /app/
RUN yarn install --production

COPY --from=builder /app/dist ./dist

EXPOSE 8000

CMD ["node", "/app/dist/index.js"]
