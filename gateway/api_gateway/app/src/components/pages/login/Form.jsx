import React from 'react';
import PropTypes from 'prop-types';
import {Field} from 'react-final-form';
import {connect} from "react-redux";

import {SimpleField, required} from "../../common";
import {Button} from "@material-ui/core";


class LoginForm extends React.Component {

  render() {
    const {handleSubmit, errors} = this.props;

    return (
      <form onSubmit={handleSubmit}>
        <Field name="email" validate={required} type="email">
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"Email"}
              submitError={errors.email}
            />
          }}
        </Field>
        <Field name="password" type="password" validate={required}>
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"Password"}
              submitError={errors.password}
            />
          }}
        </Field>
        {errors.general && <div>{errors.general}</div>}
        <div>
          <Button variant="contained" color="primary" type="submit" size="large">
            Submit
          </Button>
        </div>
      </form>
    )
  }
}

LoginForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  errors: PropTypes.object,
}


const mapStateToProps = state => ({
  errors: state.loginErrors,
});

export default connect(mapStateToProps, null)(LoginForm);
