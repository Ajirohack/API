# SpaceNew Admin Dashboard

The SpaceNew Admin Dashboard is a comprehensive web-based administration interface for managing and monitoring the SpaceNew platform.

## Features

- **Dashboard**: View system metrics, health status, and recent activity
- **Plugin Management**: Install, configure, and monitor plugins
- **Workflow Management**: Create, edit, and monitor workflows with a visual builder
- **Agent Management**: Configure and monitor AI agents in the system
- **RAG System**: Manage document ingestion, vector embeddings, and querying
- **Settings**: Configure system settings and preferences

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Access to SpaceNew backend services

### Installation

1. Clone the repository (if not already part of your SpaceNew installation)
2. Install dependencies:

```bash
cd client/admin-dashboard
npm install
```

### Development

To start the development server:

```bash
npm start
```

The dashboard will be available at <http://localhost:3000>

### Building for Production

```bash
npm run build
```

This will create an optimized build in the `build` directory that can be served by the SpaceNew system.

## Architecture

The SpaceNew Admin Dashboard is built with:

- **React**: Frontend library for building user interfaces
- **Material-UI**: Component library for consistent design
- **React Router**: For navigation between different sections
- **Axios**: For API communication with the backend
- **Chart.js**: For data visualization

## Folder Structure

```
client/admin-dashboard/
├── public/            # Static assets and HTML template
├── src/               # Source code
│   ├── components/    # Reusable UI components
│   ├── contexts/      # React contexts for state management
│   ├── hooks/         # Custom React hooks
│   ├── layouts/       # Page layouts
│   ├── pages/         # Main page components
│   ├── services/      # API service modules
│   ├── theme/         # Theme configuration
│   ├── utils/         # Utility functions
│   ├── App.js         # Application component with routing
│   └── index.js       # Entry point
└── package.json       # Dependencies and scripts
```

## API Integration

The dashboard communicates with the SpaceNew backend services through RESTful APIs. All API calls are managed through service modules in the `services/` directory.

## Authentication

The dashboard uses JWT-based authentication. Tokens are stored in the browser's localStorage and attached to API requests as needed.

## Extending the Dashboard

### Adding New Pages

1. Create a new page component in the `pages/` directory
2. Add a route in `App.js`
3. Update the navigation menu in `layouts/DashboardLayout.js`

### Adding New Features

1. Create new components in the `components/` directory
2. Create necessary API services in the `services/` directory
3. Integrate into existing pages or create new pages

## License

See the main SpaceNew license file for details.
