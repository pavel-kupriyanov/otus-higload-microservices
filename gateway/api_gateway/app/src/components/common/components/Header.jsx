import React from 'react';
import {withRouter} from "react-router-dom";
import {AppBar, Toolbar, Button} from "@material-ui/core";
import {connect} from "react-redux";
import {bindActionCreators} from "redux";
import {logout} from "../../../app/actionCreators";
import {Loader} from "../index";


class Header extends React.Component {

  constructor(props) {
    super(props);
    this.toPath = this.toPath.bind(this);
  }


  toPath(path) {
    this.props.history.push(path);
  }


  render() {
    const {isAuthenticated, logout, user} = this.props;


    return (
      <AppBar position="static">
        <Toolbar>
          <Button
            color="inherit"
            onClick={() => this.toPath('/')}>
            Social Network
          </Button>
          {isAuthenticated && <Button
            color="inherit"
            onClick={() => this.toPath('/login')}>
            {user.first_name} {user.last_name}
          </Button>}
          {isAuthenticated && <Button
            color="inherit"
            onClick={() => this.toPath('/feed')}>
            News
          </Button>}
          {isAuthenticated && <Button
            color="inherit"
            onClick={logout}>
            Logout
          </Button>}
          {!isAuthenticated && <Button
            color="inherit"
            onClick={() => this.toPath('/login')}>
            Login
          </Button>}
          {!isAuthenticated && <Button
            color="inherit"
            onClick={() => this.toPath('/register')}>
            Register
          </Button>}
          <Loader/>
        </Toolbar>
      </AppBar>
    );
  }
}


const mapStateToProps = state => ({
  isAuthenticated: state.userData.isAuthenticated,
  user: state.userData.user
});

const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    logout,
  }, dispatch)
}


export default connect(mapStateToProps, mapDispatchToProps)(withRouter(Header));
