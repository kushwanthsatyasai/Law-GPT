import React from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import Login from './screens/Login';
import Register from './screens/Register';
import Dashboard from './screens/Dashboard';
import Profile from './screens/Profile';
import UploadDoc from './screens/UploadDoc';
import DocumentAnalysis from './screens/DocumentAnalysis';
import ChatInterface from './screens/ChatInterface';
import IndianLegalResearch from './screens/IndianLegalResearch';
import './index.css';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Login /> },
      { path: 'register', element: <Register /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'profile', element: <Profile /> },
      { path: 'upload', element: <UploadDoc /> },
      { path: 'document-analysis/:documentId', element: <DocumentAnalysis /> },
      { path: 'chat', element: <ChatInterface /> },
      { path: 'chat/:sessionId', element: <ChatInterface /> },
      { path: 'indian-legal-research', element: <IndianLegalResearch /> },
    ],
  },
]);

const container = document.getElementById('root')!;
createRoot(container).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);


