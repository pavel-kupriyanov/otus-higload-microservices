import React from 'react';
import PropTypes from 'prop-types';
import {Field} from 'react-final-form';

import {SimpleField, SimpleSelect, required} from "../../common";
import {connect} from "react-redux";
import {Button} from "@material-ui/core";


class RegisterForm extends React.Component {

  render() {
    const {handleSubmit, errors} = this.props;
    const genderOptions = {"MALE": "Male", "FEMALE": "Female", "OTHER": "Other"}
    return (
      <form onSubmit={handleSubmit}>
        <Field name="email" validate={required} type="email">
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"Email"}
              placeholder={"Email"}
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
              placeholder={"Password"}
              submitError={errors.password}
            />
          }}
        </Field>
        <Field name="confirm" type="password" validate={required}>
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"Confirm password"}
              placeholder={"Confirm"}
              submitError={null}
            />
          }}
        </Field>
        <Field name="first_name" validate={required}>
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"First Name"}
              placeholder={"First Name"}
              submitError={errors.first_name}
            />
          }}
        </Field>
        <Field name="last_name">
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"Last Name"}
              placeholder={"Last Name"}
              submitError={errors.last_name}
            />
          }}
        </Field>
        <Field name="city">
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"City"}
              placeholder={"City"}
              submitError={errors.city}
            />
          }}
        </Field>
        <Field name="gender">
          {({input, meta}) => {
            return <SimpleSelect
              input={input}
              meta={meta}
              label="Gender"
              submitError={errors.gender}
              options={genderOptions}
            />
          }}
        </Field>
        <Field name="age" type="number" validate={required}>
          {({input, meta}) => {
            return <SimpleField
              input={input}
              meta={meta}
              label={"Age"}
              placeholder={"Age"}
              submitError={errors.age}
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


RegisterForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  errors: PropTypes.object.isRequired,
}


const mapStateToProps = state => ({
  errors: state.registerErrors,
});

export default connect(mapStateToProps, null)(RegisterForm);







