import React from 'react';
import PropTypes from "prop-types";
import {Card, Chip} from "@material-ui/core";
import {Link} from "react-router-dom";
import ListItemText from "@material-ui/core/ListItemText";

const style = {padding: 20, marginTop: 5};
const hobbyStyle = { marginRight: 5};


const ACTION_TYPES = {
  ADDED_FRIEND: 'ADDED_FRIEND',
  ADDED_HOBBY: 'ADDED_HOBBY',
  ADDED_POST: 'ADDED_POST'
}


export default class New extends React.Component {


  constructor(props) {
    super(props);
    this.renderNewText = this.renderNewText.bind(this);
    this.renderName = this.renderName.bind(this);
    this.renderAddedHobbyText = this.renderAddedHobbyText.bind(this);
    this.renderAddedFriendText = this.renderAddedFriendText.bind(this);
    this.renderAddedPostText = this.renderAddedPostText.bind(this);
  }

  renderNewText(newItem) {
    const {payload, type} = newItem;

    switch (type) {
      case ACTION_TYPES.ADDED_FRIEND:
        return this.renderAddedFriendText(payload);
      case ACTION_TYPES.ADDED_HOBBY:
        return this.renderAddedHobbyText(payload);
      case ACTION_TYPES.ADDED_POST:
        return this.renderAddedPostText(payload);
      default:
        return <p>{payload}</p>
    }
  }

  renderName(user) {
    const {id, first_name, last_name} = user;
    return <Link to={`/${id}`}>{first_name} {last_name ? last_name : ''}</Link>
  }

  renderAddedHobbyText(payload) {
    const {author, hobby} = payload;
    return <div>
      {this.renderName(author)} added a new hobby: <Chip label={hobby.name} style={hobbyStyle}/>
    </div>
  }

  renderAddedFriendText(payload) {
    const {author, new_friend} = payload;
    return <div>
      {this.renderName(author)} added a new friend {this.renderName(new_friend)}
    </div>
  }

  renderAddedPostText(payload) {
    const {author, text} = payload;
    return <div>
      {this.renderName(author)} written: {text}
    </div>
  }

  render() {
    const {newItem} = this.props;
    return (
      <Card style={style}>
        {this.renderNewText(newItem)}
        <ListItemText
          align="right"
          secondary={(new Date(newItem.created * 1000)).toDateString()}
        />
      </Card>
    );
  }
}

New.propTypes = {
  newItem: PropTypes.object.isRequired,
}







