# ==== CONFIGURE =====
# Use a Node 16 base image
FROM node:20-alpine  as builder
# Set the working directory to /app inside the container
WORKDIR /app
# Copy app files
COPY . .
# ==== BUILD =====
# Install dependencies (npm ci makes sure the exact versions in the lockfile gets installed)
RUN npm ci 
# Build the app
#RUN npm run build


## Bundle static assets with nginx
#FROM nginx:1.21.0-alpine as production
##FROM nginx:alpine3.17 as production
#ENV NODE_ENV production
## Copy built assets from `builder` image
#COPY --from=builder src/app/build /usr/share/nginx/html
## Add your nginx.conf
#COPY nginx.conf /etc/nginx/conf.d/default.conf
## Expose port
#EXPOSE 80
## Start nginx
#CMD ["nginx", "-g", "daemon off;"]


# ==== RUN =======
# Set the env to "production"
#ENV NODE_ENV production
# Expose the port on which the app will be running (3000 is the default that `serve` uses)
EXPOSE 3000
# Start the app
#CMD [ "npx", "serve", "build" ]
CMD [ "npm", "run", "dev" ]
#CMD [ "node", "--trace-warnings", "./node_modules/.bin/next", "dev"]


