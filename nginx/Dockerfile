FROM nginx:alpine

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy React build files into Nginx's static file directory
COPY --from=react-build /app/build /usr/share/nginx/html

# Create logs directory
RUN mkdir -p /var/log/nginx

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]