import React from 'react';
import {connect} from "react-redux";
import {bindActionCreators} from "redux";
import {Form} from "react-final-form";

import {login} from "../../../app/actionCreators";
import LoginForm from "./Form";
import {Card, Typography} from "@material-ui/core";


const style = {
  minWidth: '50%',
  minHeight: '200px',
  padding: '20px',
  margin: '40px',
  textAlign: 'center',
  justifyContent: 'center'
}

class LoginPage extends React.Component {

  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  async handleSubmit(form) {
    await this.props.login(form.email, form.password);
  }

  render() {
    return (
      <Card style={style}>
         <Typography variant="h4" component="h2">
          Login
        </Typography>
        <Form
          component={LoginForm}
          onSubmit={this.handleSubmit}
        />
      </Card>
    );
  }
}


const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    login,
  }, dispatch)
}

export default connect(null, mapDispatchToProps)(LoginPage);
