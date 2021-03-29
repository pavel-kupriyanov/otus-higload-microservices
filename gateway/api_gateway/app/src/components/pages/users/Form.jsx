import React from 'react';
import PropTypes from 'prop-types';
import {Field} from 'react-final-form';
import {Button, Card, Grid} from "@material-ui/core";

import {SimpleField} from "../../common";

const style = {
  minWidth: '100%',
  marginTop: '10px',
  marginBottom: '10px',
  textAlign: 'center',
  justifyContent: 'center'
}


export default class SearchForm extends React.Component {

  render() {
    const {handleSubmit} = this.props;

    return (
      <Card style={style}>
        <form onSubmit={handleSubmit}>
          <Grid container justify="center" spacing={1}>
            <Grid item>
              <Field name="first_name" type="text" parse={value => value || ''} initialValue={''}>
                {({input, meta}) => {
                  return <SimpleField
                    input={input}
                    meta={meta}
                    label={"First Name"}
                    placeholder={"First Name"}
                  />
                }}
              </Field>
            </Grid>
            <Grid item>
              <Field name="last_name" type="text" parse={value => value || ''} initialValue={''}>
                {({input, meta}) => {
                  return <SimpleField
                    input={input}
                    meta={meta}
                    label={"Last Name"}
                    placeholder={"Last Name"}
                  />
                }}
              </Field>
            </Grid>
            <Grid item style={{marginTop:'auto', marginBottom: 'auto'}}>
              <Button variant="contained" color="primary" type="submit" size="large">
                Submit
              </Button>
            </Grid>
          </Grid>
        </form>
      </Card>
    )
  }
}

SearchForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
}
