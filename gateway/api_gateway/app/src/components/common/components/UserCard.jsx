import React from 'react';
import PropTypes from "prop-types";
import Hobbies from "./Hobbies";
import {Card} from "@material-ui/core";
import UserInfo from "./UserInfo";

const style = {
  padding: '10px',
  height: '90%'
}


export default class UserCard extends React.Component {


  render() {
    const {user} = this.props;

    return (
      <Card style={style}>
        <UserInfo user={user}/>
        <Hobbies hobbies={user.hobbies}/>
      </Card>
    );
  }
}

UserCard.propTypes = {
  user: PropTypes.object.isRequired,
}







