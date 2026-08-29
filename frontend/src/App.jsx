import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { Dashboard } from './pages/Dashboard';
import { Cases } from './pages/Cases';
import { NewCase } from './pages/NewCase';
import { Diagnosis } from './pages/Diagnosis';
import { HumanReview } from './pages/HumanReview';
import { CaseProvider } from './context/CaseContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './components/Toast';

export function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ThemeProvider>
      <ToastProvider>
        <CaseProvider>
          <BrowserRouter>
            <div className="min-h-screen bg-slate-50 dark:bg-[#090e17] text-slate-800 dark:text-slate-100 flex flex-col antialiased font-sans transition-colors duration-200">
              {/* Responsive Collapsible Sidebar */}
              <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

              {/* Main Content Area (offset by sidebar on desktop) */}
              <div className="lg:pl-64 flex flex-col min-h-screen">
                <Topbar onMenuClick={() => setSidebarOpen(true)} />

                <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
                  <Routes>
                    {/* Default Redirect */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />

                    {/* Application Routes */}
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/cases" element={<Cases />} />
                    <Route path="/cases/:caseId" element={<Diagnosis />} />
                    <Route path="/new-case" element={<NewCase />} />
                    <Route path="/diagnosis" element={<Diagnosis />} />
                    <Route path="/diagnosis/:diagnosisId" element={<Diagnosis />} />
                    <Route path="/review" element={<HumanReview />} />
                    <Route path="/review/:diagnosisId" element={<HumanReview />} />

                    {/* 404 Catch-All */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </main>
              </div>
            </div>
          </BrowserRouter>
        </CaseProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
