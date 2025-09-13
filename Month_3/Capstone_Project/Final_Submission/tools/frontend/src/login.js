import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import UserDashboard from './UserDashboard';
import Admindashboard from './Admindashboard';

const Login = () => {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    const login = async () => {
        try {
            // Step 1: Get public IP
            const ipRes = await fetch("https://api.ipify.org?format=json");
            const ipData = await ipRes.json();
            const userIp = ipData.ip;

            // Step 2: Call backend with IP
            const res = await fetch(`http://127.0.0.1:5000/login?ip=${userIp}`);
            const data = await res.json();

            if (data.id && data.name && data.department && data.region) {
                const userData = {
                    id: data.id,
                    name: data.name,
                    department: data.department.toLowerCase(),
                    region: data.region
                };

                // ✅ Save user in state and localStorage
                setUser(userData);
                localStorage.setItem('user', JSON.stringify(userData));

                // Navigate based on role
                if (userData.department === 'admin') {
                    navigate('/Admindashboard');
                } else {
                    navigate('/UserDashboard');
                }
            } else {
                alert("Face not recognized. Please try again or register.");
                setUser(null);
            }
        } catch (err) {
            console.error("Login failed:", err);
            alert("Error during login. Check server connection.");
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
        navigate('/');
    };

    return (
        <div>
            {!user ? (
                <div className="form-group">
                    <br></br>
                    &nbsp; &nbsp; &nbsp;  &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp; &nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;

                    <input
                        type="submit"
                        value="Authenticate"
                        onClick={login}
                        className="btn btn-primary"
                    />
                </div>
            ) : (
                <div className="details">
                    <h3>Hello {user.name}!</h3>
                    <p>You are successfully logged in to the system.</p>
                    <p><strong>Department:</strong> {user.department}</p>
                    <p><strong>Region:</strong> {user.region}</p>

                    <nav>
                        <ul>
                            <div className="h">
                                <div className="d-flex align-items-left">
                                    <div className="text-end me-3" style={{ color: 'black' }}>
                                        <strong>{user.name}</strong> <small>{user.department}</small> <small>{user.region}</small>
                                    </div>
                                    <button className="btn btn-outline-danger" onClick={logout}>
                                        Logout
                                    </button>
                                    {user.department === "admin" ? (
                                        <Link to="/Admindashboard" className="nav-link"><b>AdminDashboard</b></Link>
                                    ) : (
                                        <Link to="/UserDashboard" className="nav-link"><b>UserDashboard</b></Link>
                                    )}
                                </div>
                            </div>
                        </ul>
                    </nav>
                </div>
            )}
        </div>
    );
};

export default Login;
