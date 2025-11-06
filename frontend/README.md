# Spooky RSS Frontend

A React TypeScript application for the Spooky RSS System that transforms RSS feeds into horror-themed content.

## Features

- **Dark Theme**: Atmospheric dark theme with spooky styling
- **TypeScript**: Full TypeScript support for type safety
- **React Router**: Client-side routing for navigation
- **Framer Motion**: Smooth animations and transitions
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── DarkThemeProvider/
│   ├── Navigation/
│   ├── SpookyCard/      # (to be implemented)
│   ├── FeedList/        # (to be implemented)
│   ├── GhostNotification/
│   └── PreferencesPanel/
├── hooks/               # Custom React hooks
├── pages/               # Page components
├── services/            # API services
├── types/               # TypeScript type definitions
└── App.tsx             # Main application component
```

## Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Linting

```bash
npm run lint
```

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

## Technology Stack

- **React 19**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing
- **Framer Motion**: Animations
- **Lucide React**: Icons
- **ESLint**: Code linting

## Next Steps

This is the basic structure setup. The following components need to be implemented:

1. Dark theme system with CSS variables
2. Spooky content display components
3. Ghost animations and atmospheric effects
4. User preferences panel
5. API integration with the backend