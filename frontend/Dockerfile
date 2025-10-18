FROM node:20-alpine
WORKDIR /usr/src/app
# install deps (uses your existing package.json)
COPY package.json ./
RUN npm install
# copy the rest of the frontend
COPY . .
EXPOSE 5173
CMD ["npm","run","dev","--","--host"]
