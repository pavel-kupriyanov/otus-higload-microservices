import React from 'react';
import PropTypes from "prop-types";

import Grid from "@material-ui/core/Grid";
import ListItemText from "@material-ui/core/ListItemText";
import ListItem from "@material-ui/core/ListItem";
import {Link} from "react-router-dom";
import {connect} from "react-redux";

const myMessage = {
  backgroundColor: '#F8F8FF'
}

class Message extends React.Component {


  render() {
    const {user, message, currentUser} = this.props;
    const isMyMessage = currentUser.id === user.id;
    const align = isMyMessage ? "right" : "left";
    return (
      <ListItem style={isMyMessage ? myMessage : {}}>
        <Grid container>
          <Grid item xs={12}>
            <ListItemText align={align}>
              <Link to={`/${user.id}`}>{user.first_name}</Link>
            </ListItemText>
          </Grid>
          <Grid item xs={12}>
            <ListItemText align={align} primary={message.text}/>
          </Grid>
          <Grid item xs={12}>
            <ListItemText align={align} secondary={(new Date(message.created * 1000)).toDateString()}/>
          </Grid>
        </Grid>
      </ListItem>
    );
  }
}

Message.propTypes = {
  user: PropTypes.object.isRequired,
  message: PropTypes.object.isRequired,
}

const mapStateToProps = state => ({
  currentUser: state.userData.user,
});


export default connect(mapStateToProps, null)(Message);





