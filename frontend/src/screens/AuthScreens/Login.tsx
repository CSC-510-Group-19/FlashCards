/*
MIT License

Copyright (c) 2022 John Damilola, Leo Hsiang, Swarangi Gaurkar, Kritika Javali, Aaron Dias Barreto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { isLabelWithInternallyDisabledControl } from "@testing-library/user-event/dist/utils";
import { message } from "antd";
import { useState } from "react";
import { Link } from "react-router-dom";
import Swal from "sweetalert2";
import { createWatchCompilerHost } from "typescript";
import http from 'utils/api';
import "./styles.scss";
import OAuthOptions from "components/OAuthOptions";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleEmailLogin = async(e: any) => {
    e.preventDefault();
    const payload = {
      email,
      password,
    };
    setIsSubmitting(true);

    const auth = getAuth()
    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          const user = userCredential.user;
          window.localStorage.setItem('flashCardUser', JSON.stringify(user))
          Swal.fire({
            icon: 'success',
            title: 'Login Successful!',
            text: 'You have successfully logged in',
            confirmButtonColor: '#221daf',
          }).then(() => {
            setIsSubmitting(false);
            window.location.replace("/dashboard");
          });
        })
        .catch((error) => {
            console.log("Error " + error.code + ": " + error.message);
            setIsSubmitting(false);
        })
  };

  return (
    <div className="login-page">
      <section>
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-md-5">
              <div className="login-card">
                <h3>Welcome back! 👋🏼</h3>
                <form onSubmit={handleEmailLogin}>
                  <div className="form-group">
                    <label htmlFor="email">Email address</label>
                    <input
                      type="email"
                      id="email" // Added id for the email input
                      placeholder="you@mail.com"
                      onChange={(e) => setEmail(e.target.value)}
                      className="form-control"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                      type="password"
                      id="password" // Added id for the password input
                      placeholder="password"
                      onChange={(e) => setPassword(e.target.value)}
                      className="form-control"
                      required
                    />
                  </div>
                  <button className="btn btn-main btn-block mb-3" type='submit'>
                    {isSubmitting ? 'Logging in...' : 'Login'}
                  </button>
                  <h3>Or Sign Up</h3>
                  <OAuthOptions ></OAuthOptions>
                  <p>
                    I don’t have an account?{" "}
                    <Link to="/register">Create account</Link>
                  </p>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Login;
