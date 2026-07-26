// Task 27 - Add Client-Side Routing (Completed)
import { Routes, Route } from 'react-router-dom';
// TODO: Task 29 - Implement the Backend Health Check
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import AddExpense from './pages/AddExpense';
import ExpenseList from './pages/ExpenseList';
import EditExpense from './pages/EditExpense';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/MainLayout';
import { ToastProvider } from './context/ToastContext';

function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/add" element={<AddExpense />} />
            <Route path="/expenses" element={<ExpenseList />} />
            <Route path="/edit/:id" element={<EditExpense />} />
          </Route>
        </Route>
      </Routes>
    </ToastProvider>
  );
}

export default App;
