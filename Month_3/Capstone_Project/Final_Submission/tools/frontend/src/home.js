import React, { Component } from 'react';

export default class Home extends Component {
    render() {
        return (
            <>
                <div className='NORMAL-TEXT'>Welcome...</div>                
                <br />
                
                <div>
                    <h3 className="details">Registration Process</h3>
                    <div className="details">
                        <ol>
                            <li>
                                First of all navigate to the register section from navbar of this page.
                            </li>
                            <li>
                                Start your python flask server.
                            </li>
                            <li>
                                Enter your name and click on the button which will take your image for the registration purpose which will help you log in to the system.
                            </li>
                            <li>
                                Registration is completed successfully.
                            </li>
                        </ol>
                    </div>
                </div>
                <br />
                <div>
                    <h3 className="details">Login Process</h3>
                    <div className="details">
                        <ol>
                            <li>
                                First, navigate to the login section from navbar of this page.
                            </li>
                            <li>
                                Make sure that python server is started.
                            </li>
                            <li>
                                Click on the login button which will take your image for the login purpose and will allow you to enter into the system if you are authenticated user.
                            </li>
                        </ol>
                    </div>
                </div>
            </>
        )
    }
}
