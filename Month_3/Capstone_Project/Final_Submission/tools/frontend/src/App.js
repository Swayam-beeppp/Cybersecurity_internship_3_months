import React, { Component } from "react";
import "./bootstrap.min.css";
import "./App.css";
import Register from "./Register";
import Login from "./login";
import AdminDashboard from "./Admindashboard";
import UserDashboard from "./UserDashboard";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./home";


export default class App extends Component {
  render() {
    return (
      <Router>
        <div className="light-text">
          <nav className="navbar-custom">
            <Link to="/">Home</Link>
            <Link to="/register">Register</Link>
            <Link to="/login">Login</Link>
          </nav>

          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/Admindashboard" element={<AdminDashboard />} />
            <Route path="/UserDashboard" element={<UserDashboard />} />
          </Routes>
        </div>
      </Router>
    );
  }
}
