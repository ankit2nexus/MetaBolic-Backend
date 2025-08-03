# Metabolical

A modern news web application built with React and Vite, featuring category and tag-based browsing, search functionality, and a clean, responsive UI. The app leverages React Query for efficient data fetching and caching.

## Features

- Browse news articles by category and tag
- Search for news articles
- Responsive and modern UI (light/dark mode)
- Error and loading states
- Modular component structure
- Fast development with Vite
- Data fetching and caching with React Query

## Folder Structure

```
metabolical/
├── public/                # Static assets
├── src/
│   ├── App.jsx            # Main app component with routing
│   ├── main.jsx           # Entry point, React Query setup
│   ├── index.css, App.css # Global styles
│   ├── assets/            # Images and SVGs
│   ├── components/
│   │   ├── layout/
│   │   │   └── Header.jsx
│   │   └── UI/            # Reusable UI components
│   ├── hooks/
│   │   └── useNews.js     # Custom hook for news fetching
│   ├── Pages/             # Page components (Home, Category, Tag, Search, NotFound)
│   └── utils/             # Utility functions and data
├── package.json           # Project metadata and dependencies
├── vite.config.js         # Vite configuration
├── eslint.config.js       # ESLint configuration
└── README.md              # Project documentation
```

## Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v16 or higher recommended)
- [npm](https://www.npmjs.com/) (comes with Node.js)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd metabolical
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

### Running the App Locally

1. **Start the development server:**
   ```bash
   npm run dev
   ```
   This will start the Vite development server. By default, the app will be available at [http://localhost:5173](http://localhost:5173).

2. **Open in your browser:**
   Navigate to [http://localhost:5173](http://localhost:5173) to view the app.

### Building for Production

To build the app for production:
```bash
npm run build
```
The output will be in the `dist/` folder.

To preview the production build locally:
```bash
npm run preview
```

## Project Scripts

- `npm run dev`      – Start the development server
- `npm run build`    – Build the app for production
- `npm run preview`  – Preview the production build

## Tech Stack
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [React Query](https://tanstack.com/query/latest)
- [Tailwind CSS](https://tailwindcss.com/) (assumed from class names)

