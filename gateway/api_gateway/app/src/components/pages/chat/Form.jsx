import React from 'react';
import PropTypes from 'prop-types';
import {Field} from 'react-final-form';
import {Button, Grid} from "@material-ui/core";

import {SimpleField} from "../../common";
import Paper from "@material-ui/core/Paper";

const style = {
  minWidth: '100%',
  marginTop: 10,
  marginBottom: 10,
}


export default class MessageForm extends React.Component {

  render() {
    const {handleSubmit, form, submitting, pristine} = this.props;

    return (
      <form onSubmit={async event => {await handleSubmit(event);form.reset()}} style={style}>
        <Grid container component={Paper}>
          <Grid item xs={10}>
            <Field name="text">
              {({input, meta}) => {
                return <SimpleField input={input} meta={meta} style={{minWidth: '90%'}} label="Message"/>
              }}
            </Field>
          </Grid>
          <Grid item xs={2} style={{marginTop: 'auto', marginBottom: 'auto'}}>
            <Button
              variant="contained"
              color="primary"
              type="submit"
              size="large"
              disabled={submitting || pristine}>
              Send
            </Button>
          </Grid>
        </Grid>
      </form>
    )
  }
}

MessageForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
}
