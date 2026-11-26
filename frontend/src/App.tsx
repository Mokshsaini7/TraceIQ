import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { SubmitBugPage } from './pages/SubmitBugPage';
import { BugReportsPage } from './pages/BugReportsPage';
import { SubmissionDetailsPage } from './pages/SubmissionDetailsPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { SemanticSearchPage } from './pages/SemanticSearchPage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { SettingsPage } from './pages/SettingsPage';
import { NotFoundPage } from './pages/NotFoundPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<LandingPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="submit" element={<SubmitBugPage />} />
          <Route path="reports" element={<BugReportsPage />} />
          <Route path="reports/:id" element={<SubmissionDetailsPage />} />
          <Route path="knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="search" element={<SemanticSearchPage />} />
          <Route path="architecture" element={<ArchitecturePage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
