import React, { Component } from 'react';
import { useNavigate } from 'react-router-dom';

class RegisterClass extends Component {
    constructor() {
        super();
        this.state = {
            name: '',
            id: null,
            department: '',
            region: '',
            stage: 1,
            result_status: null,
            error: null,
            isLoading: false
        };
    }

    register = () => {
        const { name } = this.state;

        if (!name.trim()) {
            this.setState({ error: "Name is required." });
            return;
        }

        this.setState({ isLoading: true, error: null });

        fetch(`http://127.0.0.1:5000/register?name=${encodeURIComponent(name)}`)
            .then(res => res.json())
            .then(res => {
                if (res.id) {
                    this.setState({
                        id: res.id,
                        name: res.name,
                        stage: 2,
                        isLoading: false
                    });
                } else {
                    throw new Error("Failed to register. Try again.");
                }
            })
            .catch(err => {
                this.setState({ error: err.message, isLoading: false });
            });
    };

    submitDetails = () => {
        const { id, department, region } = this.state;

        if (!department.trim() || !region.trim()) {
            this.setState({ error: "Both department and region are required." });
            return;
        }

        this.setState({ isLoading: true, error: null });

        fetch("http://127.0.0.1:5000/register/details", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ id, department, region })
        })
            .then(res => res.text())
            .then(res => {
                this.setState({ result_status: res, isLoading: false }, () => {
                    setTimeout(() => {
                        this.props.navigate(`/UserDashboard`);
                    }, 2000); // Redirect after 2 seconds
                });
            })
            .catch(err => {
                this.setState({ error: "Failed to submit details. Try again.", isLoading: false });
            });
    };

    render() {
        const {
            stage,
            name,
            department,
            region,
            result_status,
            error,
            isLoading
        } = this.state;

        if (result_status) {
            return (
                <div className="details mt-4">
                    ✅ Hello <strong>{name}</strong>!<br />
                    Registration complete with department <strong>{department}</strong> and region <strong>{region}</strong>.<br />
                    Redirecting to your dashboard...
                </div>
            );
        }

        return (
            <>
                {error && <div className="alert alert-danger">{error}</div>}

                {stage === 1 && (
                    <>
                        <div className="form-group">
                            <label>Enter your name</label>
                            <input
                                type="text"
                                className="form-control"
                                value={name}
                                onChange={(e) => this.setState({ name: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <input
                                type="submit"
                                value={isLoading ? "Capturing..." : "Capture Face"}
                                onClick={this.register}
                                className="btn btn-primary"
                                disabled={isLoading}
                            />
                        </div>
                    </>
                )}

                {stage === 2 && (
                    <>
                        <div className="form-group">
                            <label>Enter your Department</label>
                            <input
                                type="text"
                                className="form-control"
                                value={department}
                                onChange={(e) => this.setState({ department: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>Enter your Region</label>
                            <input
                                type="text"
                                className="form-control"
                                value={region}
                                onChange={(e) => this.setState({ region: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <input
                                type="submit"
                                value={isLoading ? "Submitting..." : "Submit Details"}
                                onClick={this.submitDetails}
                                className="btn btn-success"
                                disabled={isLoading}
                            />
                        </div>
                    </>
                )}
            </>
        );
    }
}

// Functional wrapper to use useNavigate in class component
export default function Register(props) {
    const navigate = useNavigate();
    return <RegisterClass {...props} navigate={navigate} />;
}
