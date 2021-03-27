import React from 'react';
import {connect} from "react-redux";

import {Snackbar} from "@material-ui/core";


class Notification extends React.Component {


  render() {
    const {message} = this.props;

    return <Snackbar
      open={!!message}
      anchorOrigin={{vertical: 'top', horizontal: 'right'}}
      message={message}
      severity="error"
    />
  }
}


const mapStateToProps = state => ({
  message: state.message,
});


export default connect(mapStateToProps, null)(Notification);
