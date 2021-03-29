import React from 'react';
import {Redirect} from "react-router-dom";
import PropTypes from "prop-types";
import {connect} from "react-redux";


class AnonymousOnly extends React.Component {


  render() {
    const {userData} = this.props;
    const redirect = userData && userData.isAuthenticated;
    return (
      <React.Fragment>
        {redirect ? <Redirect to={{pathname: `/${userData.authentication.user_id}`}}/> :
          this.props.children}
      </React.Fragment>
    );
  }
}


AnonymousOnly.propTypes = {
  userData: PropTypes.object.isRequired,
}


const mapStateToProps = state => ({
  userData: state.userData,
});


export default connect(mapStateToProps, null)(AnonymousOnly);
