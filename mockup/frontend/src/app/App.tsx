import { Outlet } from "react-router-dom";

import { AppHeader } from "../components/layout/AppHeader";
import { PageContainer } from "../components/layout/PageContainer";

export function App() {
  return (
    <PageContainer>
      <AppHeader />
      <Outlet />
    </PageContainer>
  );
}