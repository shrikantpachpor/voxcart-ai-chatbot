# 🛍️ E-Commerce Chatbot Frontend

A modern, interactive e-commerce platform with an integrated AI chatbot for enhanced customer experience. Built with React, TypeScript, Redux Toolkit, and Tailwind CSS.

## ✨ Features

- 🤖 **AI-Powered Chatbot** - Intelligent shopping assistant for product recommendations and customer support
- 🛒 **Shopping Cart** - Dynamic cart management with real-time updates
- 👤 **User Authentication** - Secure login and registration system
- 💳 **Payment Integration** - Multiple payment methods support
- 📦 **Order Tracking** - Real-time order status updates
- 📱 **Responsive Design** - Optimized for all devices
- 🎨 **Modern UI** - Built with Tailwind CSS for a sleek interface

## 🚀 Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Redux Toolkit** - State management with Redux Persist
- **Vite** - Fast build tool and dev server
- **Tailwind CSS 4** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v16 or higher)
- npm or yarn package manager

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/voxcart-frontend.git
   cd voxcart-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and update the API base URL:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

   The app will open at [http://localhost:5173](http://localhost:5173)

## 📜 Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start development server with Vite |
| `npm run build` | Build for production |
| `npm run serve` | Preview production build |
| `npm test` | Run test suite |
| `npm run coverage` | Generate test coverage report |
| `npm run lint` | Lint code with ESLint |
| `npm run format` | Format code with Prettier |

## 🏗️ Project Structure

```
src/
├── components/          # Reusable React components
│   ├── Auth/           # Authentication components
│   ├── Cart/           # Shopping cart components
│   ├── Chat/           # Chatbot components
│   ├── Layout/         # Layout components (Navbar, etc.)
│   ├── Order/          # Order tracking components
│   ├── Products/       # Product display components
│   └── Profile/        # User profile components
├── pages/              # Page components
├── services/           # API services and HTTP clients
├── store/              # Redux store configuration
│   ├── slices/        # Redux slices (auth, chat, etc.)
│   └── types/         # TypeScript type definitions
└── utils/              # Utility functions
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

### Tailwind CSS

Customize the design system in `tailwind.config.js`

### Vite Configuration

Build settings can be modified in `vite.config.js`

## 🧪 Testing

Run the test suite:
```bash
npm test
```

Generate coverage report:
```bash
npm run coverage
```

## 📦 Building for Production

Create an optimized production build:
```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

Preview the production build locally:
```bash
npm run serve
```

## 🚀 Deployment

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
# Deploy the dist/ folder to Netlify
```

### Environment Variables for Production

Make sure to set the following environment variables in your deployment platform:
- `VITE_API_BASE_URL` - Your production API URL

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**VoxCart Contributors**

## 🙏 Acknowledgments

- React team for the amazing framework
- Redux Toolkit for simplified state management
- Tailwind CSS for the utility-first CSS framework
- Vite for the blazing-fast build tool

## 📞 Support

For support, please open an issue in the GitHub repository.

---

Made with ❤️ by VoxCart Contributors
