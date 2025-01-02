import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    // this ensures that the browser opens upon server start
    open: true,
    // this sets a default port to 3000  
    port: 3000, 
    // If you need to proxy API requests during development
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  // You can also configure build options, aliases, etc.
});

// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'
// import viteTsconfigPaths from 'vite-tsconfig-paths'

// export default defineConfig({
//     // depending on your application, base can also be "/"
//     base: '',
//     plugins: [react(), viteTsconfigPaths()],
//     server: {    
//         // this ensures that the browser opens upon server start
//         open: true,
//         // this sets a default port to 3000  
//         port: 3000, 
//         proxy: {
//             '/api': 'http://localhost:8000',
//         },
//     },
// })