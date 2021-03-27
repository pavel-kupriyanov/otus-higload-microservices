import React from 'react';
import PropTypes from "prop-types";
import {Button} from "@material-ui/core";


export default class PaginateButtons extends React.Component {

  render() {
    const {page, isAll, handlePage} = this.props;
    return <>
      {(page > 1) && <Button
        variant="contained"
        color="primary"
        type="submit"
        size="large"
        style={{marginRight: '10px'}}
        onClick={() => handlePage(page - 1)}>
        Previous
      </Button>}
      {!isAll && <Button
        variant="contained"
        color="primary"
        type="submit"
        size="large"
        style={{marginRight: '10px'}}
        onClick={() => handlePage(page + 1)}>
        Next
      </Button>}
    </>
  }
}

PaginateButtons.propTypes = {
  page: PropTypes.number.isRequired,
  isAll: PropTypes.bool.isRequired,
  handlePage: PropTypes.func.isRequired
}







