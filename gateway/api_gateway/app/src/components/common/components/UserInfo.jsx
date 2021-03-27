import React from 'react';
import PropTypes from "prop-types";
import {Link} from "react-router-dom";
import UserStatus from "./UserStatus";
import {Typography, Button} from "@material-ui/core";
import {connect} from "react-redux";


const typographyStyle = {
  display: 'flex',
  justifyContent: 'space-between'
}


class UserInfo extends React.Component {


  render() {
    const {user, isAuthenticated} = this.props;

    return <>
      <Typography variant="h6" component="h2" style={typographyStyle}>
        <Link to={`/${user.id}`}>{user.first_name} {user.last_name}</Link>
        {isAuthenticated && <UserStatus user={user}/>}
      </Typography>
      {isAuthenticated && <Link to={`/chat/${user.id}`}>
        <Button variant="contained" color="primary">Chat</Button>
      </Link>}

      <p><b>Age:</b> {user.age}</p>
      {user.city && <p><b>City:</b> {user.city}</p>}
      {user.gender && <p><b>Gender:</b> {user.gender}</p>}
    </>
  }
}

UserInfo.propTypes = {
  user: PropTypes.object.isRequired,
}


const mapStateToProps = state => ({
  isAuthenticated: state.userData.isAuthenticated,
});


export default connect(mapStateToProps, null)(UserInfo);







