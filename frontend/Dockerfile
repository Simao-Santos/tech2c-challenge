FROM node:18-alpine

# Set docker related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

COPY package*.json ./
RUN npm i

COPY . /app/

CMD ["npm", "run", "dev"]