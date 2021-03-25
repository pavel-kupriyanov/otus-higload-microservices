import React from "react";
import {bindActionCreators} from "redux";
import {deleteFriendship} from "../../../../app/actionCreators";
import {connect} from "react-redux";
import PropTypes from "prop-types";
import {Chip} from "@material-ui/core";


class Friend extends React.Component {

  constructor(props) {
    super(props);
    this.handleDelete = this.handleDelete.bind(this);
  }

  handleDelete() {
    const {user, deleteFriendship} = this.props;
    deleteFriendship(user.id);
  }

  render() {
    return <Chip label="Friend" onDelete={this.handleDelete} color="primary"/>
  }
}

Friend.propTypes = {
  user: PropTypes.object.isRequired,
}


const mapDispatchToProps = dispatch => {
  return bindActionCreators({
    deleteFriendship,
  }, dispatch)
}

export default connect(null, mapDispatchToProps)(Friend);
