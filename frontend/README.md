# Spooky RSS Frontend

A React TypeScript application for the Spooky RSS System that transforms RSS feeds into horror-themed content.

## Features

- **Dark Theme**: Atmospheric dark theme with spooky styling
- **TypeScript**: Full TypeScript support for type safety
- **React Router**: Client-side routing for navigation
- **Framer Motion**: Smooth animations and transitions
- **Responsive Design**: Works on desktop and mobile devices
- **Data Persistence**: Automatic localStorage persistence for feeds and preferences
- **Data Management**: Export, import, and clear your haunted data

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

## Data Persistence

The app automatically saves all your feeds and preferences to browser localStorage. See [DATA_PERSISTENCE.md](./DATA_PERSISTENCE.md) for detailed information about:

- How data is stored and retrieved
- Export/import functionality
- Data management tools
- Storage limits and best practices

## Key Features Implemented

✅ Dark theme system with CSS variables
✅ Spooky content display components
✅ Ghost animations and atmospheric effects
✅ User preferences panel with persistence
✅ API integration with the backend
✅ Data persistence with localStorage
✅ Export/import functionality