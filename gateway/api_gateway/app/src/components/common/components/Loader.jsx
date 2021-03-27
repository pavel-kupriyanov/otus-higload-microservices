import React from 'react';
import {connect} from "react-redux";
import {CircularProgress} from "@material-ui/core";



class Loader extends React.Component {


  render() {

    return (
      <>
        {!!this.props.requestCount && <CircularProgress color="inherit"/>}
      </>
    );
  }
}


const mapStateToProps = state => ({
  requestCount: state.requestCount,
});


export default connect(mapStateToProps, null)(Loader);
