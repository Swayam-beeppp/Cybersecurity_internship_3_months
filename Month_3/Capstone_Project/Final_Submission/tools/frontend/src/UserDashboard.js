import React, { useEffect, useState } from 'react';
import ".//user.css";

const UserDashboard = () => {
    const [user, setUser] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [attendance, setAttendance] = useState([]);
    const [loginHistory, setLoginHistory] = useState([]);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            const parsedUser = JSON.parse(storedUser);
            setUser(parsedUser);
            console.log('User data:', parsedUser);

            const userId = parsedUser.id;

            fetch(`http://localhost:5000/get-tasks/${userId}`)
                .then(res => res.json())
                .then(data => setTasks(data))
                .catch(err => console.error("Error fetching tasks:", err));

            fetch(`http://localhost:5000/get-attendance/${userId}`)
                .then(res => res.json())
                .then(data => setAttendance(data))
                .catch(err => console.error("Error fetching attendance:", err));

            fetch(`http://localhost:5000/get-login-history/${userId}`)
                .then(res => res.json())
                .then(data => setLoginHistory(data))
                .catch(err => console.error("Error fetching login history:", err));
        } else {
            // Redirect if no user data found
            window.location.href = "/login";
        }
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('user');
        window.location.href = "/login";
    };

    return (
        <div>
            <h2>User Dashboard</h2>
            <button onClick={handleLogout} style={{ marginBottom: "20px", padding: "8px 16px", cursor: "pointer" }}>
                Logout
            </button>

            {user ? (
                <div>
                    <h3>User Information</h3>
                    <p><strong>ID:</strong> {user.id}</p>
                    <p><strong>Name:</strong> {user.name}</p>
                    <p><strong>Department:</strong> {user.department}</p>
                    <p><strong>Region:</strong> {user.region}</p>
                </div>
            ) : (
                <p>Loading user data...</p>
            )}

            <h3>Tasks</h3>
            {tasks.length > 0 ? (
                <table border="1">
                    <thead>
                        <tr>
                            <th>Task ID</th>
                            <th>Task Name</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tasks.map(task => (
                            <tr key={task.id}>
                                <td>{task.id}</td>
                                <td>{task.task_name}</td>
                                <td>{task.status}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>Loading tasks...</p>
            )}

            <h3>Attendance</h3>
            {attendance.length > 0 ? (
                <table border="1">
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {attendance.map(item => (
                            <tr key={item.id}>
                                <td>{item.user_id}</td>
                                <td>{item.present_days}</td>
                                <td>{item.total_days}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>Loading attendance...</p>
            )}

            <h3>Login History</h3>
            {loginHistory.length > 0 ? (
                <table
                    border="1"
                    style={{
                        borderCollapse: "collapse",
                        width: "90%",
                        margin: "20px auto",
                        fontFamily: "Arial, sans-serif",
                        boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
                    }}
                >
                    <thead>
                        <tr style={{ backgroundColor: "#4CAF50", color: "white", textTransform: "uppercase" }}>
                            <th style={{ padding: "12px", border: "1px solid #ddd" }}>Login ID</th>
                            <th style={{ padding: "12px", border: "1px solid #ddd" }}>User ID</th>
                            <th style={{ padding: "12px", border: "1px solid #ddd" }}>Login Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loginHistory.map(item => (
                            <tr
                                key={item.id}
                                style={{
                                    textAlign: "center",
                                }}
                            >
                                <td style={{ padding: "10px", border: "1px solid #ddd" }}>{item.id}</td>
                                <td style={{ padding: "10px", border: "1px solid #ddd" }}>{item.user_id}</td>
                                <td style={{ padding: "10px", border: "1px solid #ddd" }}>{item.time}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p style={{ textAlign: "center" }}>No login history available.</p>
            )}
        </div>
    );
};

export default UserDashboard;
