---
description: Work in progress
---

# The GetBeaned API

{% api-method method="post" host="https://getbeaned.api-d.com" path="/api/users/" %}
{% api-method-summary %}
Add an user
{% endapi-method-summary %}

{% api-method-description %}
This endpoint allows you to upload an user data to the website. This is a required step to be able to add actions.  
  
The endpoint will update or create the user automatically.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-headers %}
{% api-method-parameter name="Update" type="boolean" required=false %}
False if we don't want to update the user because the data is stale
{% endapi-method-parameter %}

{% api-method-parameter name="Authentication" type="string" required=true %}
Authentication token supplied on request.
{% endapi-method-parameter %}
{% endapi-method-headers %}

{% api-method-form-data-parameters %}
{% api-method-parameter name="discord\_default\_avatar\_url" type="string" required=true %}
Default Discord CDN URL for the user avatar.
{% endapi-method-parameter %}

{% api-method-parameter name="discord\_avatar\_url" type="string" required=true %}
Discord CDN URL to the PNG \(static\) or WEBP \(animated\) avatar of the user
{% endapi-method-parameter %}

{% api-method-parameter name="discord\_discriminator" type="integer" required=true %}
The user Discriminator \(Excluding the `#`\)
{% endapi-method-parameter %}

{% api-method-parameter name="discord\_name" type="string" required=true %}
Name of the user
{% endapi-method-parameter %}

{% api-method-parameter name="discord\_id" type="boolean" required=true %}
Discord user ID
{% endapi-method-parameter %}

{% api-method-parameter name="discord\_bot" type="boolean" required=true %}
Please set that to True if the user is a bot
{% endapi-method-parameter %}
{% endapi-method-form-data-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}
Cake successfully retrieved.
{% endapi-method-response-example-description %}

```javascript
{
 'status': 'ok',
 'message': 'User existed in database already',
 'result': '[User representation]'
 }
```
{% endapi-method-response-example %}

{% api-method-response-example httpCode=302 %}
{% api-method-response-example-description %}
Error when saving the new user
{% endapi-method-response-example-description %}

```javascript
{
    'status': 'error',
    'errors': ['List of errors']
}
```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="get" host="https://getbeaned.api-d.com" path="/api/users/<int:guild\_id>/<int:user\_id>/counters/" %}
{% api-method-summary %}
Api Users Counter
{% endapi-method-summary %}

{% api-method-description %}

{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="" type="string" required=false %}

{% endapi-method-parameter %}
{% endapi-method-path-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

