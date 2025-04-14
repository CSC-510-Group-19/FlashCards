import AuthLayout from 'layouts/AuthLayout'
import DashboardLayout from 'layouts/DashboardLayout'
import HomeLayout from 'layouts/HomeLayout'
import { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router'
import { authRoutes, dashboardRoutes, homeRoutes, publicRoutes } from './routes'
import "swiper/css/bundle";
import 'bootstrap/dist/css/bootstrap.css';
import './initializeFirebase'
import { getAuth, onAuthStateChanged, getIdToken } from "firebase/auth";
import http from "utils/api"

const App = () => {
  const location = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location])

  const flashCardUser = window.localStorage.getItem('flashCardUser');
  const isAuth = flashCardUser && JSON.parse(flashCardUser) ? true : false;

  const auth = getAuth()
  onAuthStateChanged(auth, (user) => {
    if (user) {
      // User is signed in, get the ID token
      user.getIdToken().then((idToken) => {
        // Send the ID token to your backend or use it for other purposes
        console.log(idToken);
        window.localStorage.setItem('idToken', idToken);
      }).catch((error) => {
        // Handle error
        console.error(error);
      });
    } else {
      // User is signed out
    }
  });

  return (
    <>
      <Routes>
        <Route element={<HomeLayout />}>
          {homeRoutes.map(({ path, element }: any, index: number) => (
            <Route path={path} element={element} key={index} />
          ))}
        </Route>

        <Route element={isAuth ? <DashboardLayout /> : <HomeLayout />}>
          {publicRoutes.map(({ path, element }: any, index: number) => (
              <Route path={path} element={element} key={index} />
          ))}
        </Route>

        <Route element={<AuthLayout />}>
          {authRoutes.map(({ path, element }: any, index: number) => (
            <Route path={path} element={element} key={index} />
          ))}
        </Route>

        <Route element={<DashboardLayout />}>
          {dashboardRoutes.map(({ path, element }: any, index: number) => (
            <Route path={path} element={element} key={index} />
          ))}
        </Route>
      </Routes>
    </>
  )
}

export default App