import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const MainLayout = () => {
  // Using a very simplified approach for responsive layout width.
  // The Sidebar has a fixed position. We just need to give the main content area 
  // a left margin so it isn't hidden under the Sidebar.
  // To match the Sidebar's 'w-20' and 'w-64', we can rely on a media query or a state context.
  // However, since Sidebar tracks its own state, a simpler global CSS approach is padding-left
  // that aligns with the typical width, or we can lift the collapsed state up if needed.
  // For Gemini style, we often just use flex layout if we lift state, or just let Sidebar be absolute
  // and overlap or push. Let's lift state here for a cleaner layout push.

  const [isSidebarCollapsed, setIsSidebarCollapsed] = React.useState(false);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar is fixed, but we need to pass down the state and setter if we wanted to lift it.
          Let's just use the Sidebar as a child and manage state locally in it, while 
          the main area adds a generic left margin for desktop. 
          Wait, if Sidebar manages its own width, we can't easily animate the margin without context.
          Let's lift state so MainLayout controls the width. */}
      
      {/* For simplicity, we'll render Sidebar and pass props, modifying Sidebar to accept them.
          Actually, since I just wrote Sidebar to manage its own state, let's just make the main 
          content area flex-1 and add a spacer div that reacts to a ResizeObserver or just 
          have Sidebar pass its state up.
          Let's just use a fixed margin of pl-20 (80px) and let the sidebar overlap when expanded
          like a drawer. Gemini does push the content, so lifting state is best. */}
          
      {/* To keep changes minimal without rewriting Sidebar right away, we will wrap Outlet 
          in a main tag that has pl-20 md:pl-64 depending on state. */}
      <Sidebar onToggle={(collapsed) => setIsSidebarCollapsed(collapsed)} />
      
      <main className={`flex-1 transition-all duration-300 ${isSidebarCollapsed ? 'ml-20' : 'ml-64'}`}>
        {/* Added standard padding inside the main content */}
        <div className="h-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
