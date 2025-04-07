import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
        ranking: path.resolve(__dirname, 'ranking.html'), // 👈 加上这个
      },
    },
  },
})
