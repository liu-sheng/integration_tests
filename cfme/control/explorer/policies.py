# -*- coding: utf-8 -*-
"""Page model for Control / Explorer"""
from navmazing import NavigateToAttribute, NavigateToSibling
from widgetastic_patternfly import Button, Input
from widgetastic.utils import Version, VersionPick
from widgetastic.widget import Text, Checkbox, TextInput, View

from . import ControlExplorerView
from actions import Action
from cfme.web_ui.expression_editor_widgetastic import ExpressionEditor
from cfme.utils import ParamClassName
from cfme.utils.appliance import NavigatableMixin
from cfme.utils.appliance.implementations.ui import navigator, navigate_to, CFMENavigateStep
from cfme.utils.pretty import Pretty
from cfme.utils.update import Updateable
from widgetastic_manageiq import (
    BootstrapSwitchSelect, CheckboxSelect, MultiBoxSelect, SummaryFormItem, Dropdown)


class PoliciesAllView(ControlExplorerView):
    title = Text("#explorer_title_text")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == "All {} {} Policies".format(
                self.context["object"].PRETTY,
                self.context["object"].TYPE
            )
        )


class EditPolicyEventAssignments(ControlExplorerView):
    title = Text("#explorer_title_text")

    events = VersionPick({
        Version.lowest(): CheckboxSelect("policy_info_div"),
        "5.8.1": BootstrapSwitchSelect("policy_info_div")
    })

    cancel_button = Button("Cancel")
    save_button = Button("Save")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == 'Editing {} {} Policy "{}" Event Assignments'.format(
                self.context["object"].PRETTY,
                self.context["object"].TYPE,
                self.context["object"].description
            )
        )


class EditPolicyConditionAssignments(ControlExplorerView):
    title = Text("#explorer_title_text")
    conditions = MultiBoxSelect()
    cancel_button = Button("Cancel")
    save_button = Button("Save")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == 'Editing {} {} Policy "{}" Condition Assignments'.format(
                self.context["object"].PRETTY,
                self.context["object"].TYPE,
                self.context["object"].description
            )
        )


class PolicyFormCommon(ControlExplorerView):

    description = Input(name="description")
    active = Checkbox("active")
    scope = ExpressionEditor()
    notes = TextInput(name="notes")

    cancel_button = Button("Cancel")


class NewPolicyView(PolicyFormCommon):
    title = Text("#explorer_title_text")

    add_button = Button("Add")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == "Adding a new {} {} Policy".format(
                self.context["object"].PRETTY, self.context["object"].TYPE) and
            self.policies.is_opened and
            self.policies.tree.currently_selected == ["All {} {} Policies".format(
                self.context["object"].PRETTY, self.context["object"].TYPE)]
        )


class EditPolicyView(PolicyFormCommon):
    title = Text("#explorer_title_text")

    save_button = Button("Save")
    reset_button = Button("Reset")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == 'Editing {} {} Policy "{}"'.format(
                self.context["object"].PRETTY,
                self.context["object"].TYPE,
                self.context["object"].description
            ) and
            self.policies.is_opened and
            self.policies.tree.currently_selected == [
                "All Policies",
                "{} Policies".format(self.context["object"].TYPE),
                "{} {} Policies".format(self.context["object"].TREE_NODE,
                    self.context["object"].TYPE),
                self.context["object"].description
            ]
        )


class PolicyDetailsView(ControlExplorerView):
    title = Text("#explorer_title_text")

    type = SummaryFormItem("Basic Information", "Action Type")
    analysis_profile = SummaryFormItem("Analysis Profile", "Assigned Analysis Profile")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == '{} {} Policy "{}"'.format(self.context["object"].PRETTY,
                self.context["object"].TYPE, self.context["object"].description) and
            self.policies.is_opened and
            self.policies.tree.currently_selected == [
                "All Policies",
                "{} Policies".format(self.context["object"].TYPE),
                "{} {} Policies".format(self.context["object"].TREE_NODE,
                    self.context["object"].TYPE),
                self.context["object"].description
            ]
        )


class ConditionDetailsView(ControlExplorerView):
    title = Text("#explorer_title_text")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == '{} Condition "{}"'.format(self.context["object"].PRETTY,
                self.context["object"].testing_condition.description) and
            self.policies.is_opened and
            self.policies.tree.currently_selected == [
                "All Policies",
                "{} Policies".format(self.context["object"].TYPE),
                "{} {} Policies".format(self.context["object"].TREE_NODE,
                    self.context["object"].TYPE),
                self.context["object"].description,
                self.context["object"].testing_condition.description
            ]
        )


class EventDetailsToolbar(View):
    """Toolbar widets on the event details page"""
    configuration = Dropdown('Configuration')


class EventDetailsView(ControlExplorerView):
    title = Text("#explorer_title_text")
    toolbar = View.nested(EventDetailsToolbar)

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == 'Event "{}"'.format(self.context["object"].testing_event)
        )


class EditEventView(ControlExplorerView):
    title = Text("#explorer_title_text")

    true_actions = MultiBoxSelect(
        move_into="choices_chosen_true_div",
        move_from="members_chosen_true_div",
        available_items="choices_chosen_true",
        chosen_items="members_chosen_true"
    )

    false_actions = MultiBoxSelect(
        move_into="choices_chosen_false_div",
        move_from="members_chosen_false_div",
        available_items="choices_chosen_false",
        chosen_items="members_chosen_false"
    )

    save_button = Button("Save")
    reset_button = Button("Reset")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return (
            self.in_control_explorer and
            self.title.text == 'Editing Event "{}"'.format(self.context["object"].testing_event)
        )


class PolicyCollection(NavigatableMixin):

    def __init__(self, parent=None, appliance=None):
        if parent is None and appliance is None or parent and appliance:
            raise ValueError("You should provider either parent or appliance")
        self.parent = parent
        self.appliance = getattr(self.parent, "appliance", appliance)

    def instantiate(self, description, policy_class, active=True, scope=None, notes=None):
        return policy_class(description, self, active=active, scope=scope, notes=notes)

    def create(self, description, policy_class, active=True, scope=None, notes=None):
        policy = self.instantiate(description, policy_class, active=active, scope=scope,
            notes=notes)
        view = navigate_to(policy, "Add")
        view.fill({
            "description": policy.description,
            "active": policy.active,
            "scope": policy.scope,
            "notes": policy.notes
        })
        view.add_button.click()
        view = policy.create_view(PolicyDetailsView)
        assert view.is_displayed
        view.flash.assert_success_message('Policy "{}" was added'.format(policy.description))
        return policy

    def all(self):
        pass


class BasePolicy(Updateable, NavigatableMixin, Pretty):
    """This class represents a Policy.

    Example:
        .. code-block:: python

          >>> from cfme.control.explorer.policy import VMCompliancePolicy
          >>> policy = VMCompliancePolicy("policy_description")
          >>> policy.create()
          >>> policy.delete()

    Args:
        description: Policy name.
        active: Whether the policy active or not.
        scope: Policy scope.
        notes: Policy notes.
    """

    TYPE = None
    TREE_NODE = None
    PRETTY = None
    _param_name = ParamClassName('description')

    def __init__(self, description, collection, active=True, scope=None, notes=None):
        self.collection = collection
        self.appliance = self.collection.appliance
        self.description = description
        self.active = active
        self.scope = scope
        self.notes = notes

    def __str__(self):
        return self.description

    @property
    def name_for_policy_profile(self):
        return "{} {}: {}".format(self.PRETTY, self.TYPE, self.description)

    @property
    def parent(self):
        return self.collection.parent

    @property
    def policy_profile(self):
        return self.parent.policy_profile

    @property
    def conditions(self):
        pass

    @property
    def events(self):
        pass

    def update(self, updates):
        """Update this Policy in UI.

        Args:
            updates: Provided by update() context manager.
            cancel: Whether to cancel the update (default False).
        """
        view = navigate_to(self, "Edit")
        changed = view.fill(updates)
        if changed:
            view.save_button.click()
        else:
            view.cancel_button.click()
        view = self.create_view(PolicyDetailsView, override=updates)
        assert view.is_displayed
        view.flash.assert_no_error()
        if changed:
            view.flash.assert_message(
                'Policy "{}" was saved'.format(updates.get("description", self.description)))
        else:
            view.flash.assert_message(
                'Edit of Policy "{}" was cancelled by the user'.format(self.description))

    def delete(self, cancel=False):
        """Delete this Policy in UI.

        Args:
            cancel: Whether to cancel the deletion (default False).
        """
        view = navigate_to(self, "Details")
        view.configuration.item_select("Delete this {} Policy".format(self.PRETTY),
            handle_alert=not cancel)
        if cancel:
            assert view.is_displayed
            view.flash.assert_no_error()
        else:
            view = self.create_view(PoliciesAllView)
            assert view.is_displayed
            view.flash.assert_no_error()

    def copy(self, cancel=False):
        """Copy this Policy in UI.

        Args:
            cancel: Whether to cancel the copying (default False).
        """
        view = navigate_to(self, "Details")
        view.configuration.item_select("Copy this {} Policy".format(self.PRETTY),
            handle_alert=not cancel)
        view = self.create_view(PolicyDetailsView)
        assert view.is_displayed
        view.flash.assert_success_message('Policy "Copy of {}" was added'.format(self.description))
        return type(self)("Copy of {}".format(self.description))

    def assign_events(self, *events, **kwargs):
        """Assign events to this Policy.

        Args:
            events: Events which need to be assigned.
            extend: Do not uncheck existing events.
        """
        events = list(events)
        extend = kwargs.pop("extend", False)
        if extend:
            events += self.assigned_events
        view = navigate_to(self, "Details")
        view.configuration.item_select("Edit this Policy's Event assignments")
        view = self.create_view(EditPolicyEventAssignments)
        assert view.is_displayed
        changed = view.fill({"events": events})
        if changed:
            view.save_button.click()
        else:
            view.cancel_button.click()
        view.flash.assert_success_message('Policy "{}" was saved'.format(self.description))

    def is_event_assigned(self, event):
        return event in self.assigned_events

    def assign_conditions(self, *conditions):
        """Assign conditions to this Policy.

        Args:
            conditions: Conditions which need to be assigned.
        """
        view = navigate_to(self, "Details")
        view.configuration.item_select("Edit this Policy's Condition assignments")
        view = self.create_view(EditPolicyConditionAssignments)
        assert view.is_displayed
        changed = view.fill({"conditions": [condition.description for condition in conditions]})
        if changed:
            view.save_button.click()
        else:
            view.cancel_button.click()
        view.flash.assert_success_message('Policy "{}" was saved'.format(self.description))

    def is_condition_assigned(self, condition):
        self.testing_condition = condition
        view = navigate_to(self, "Condition Details")
        return view.is_displayed

    def assign_actions_to_event(self, event, actions):
        """
        This method takes a list or dict of actions, goes into the policy event and assigns them.
        Actions can be passed both as the objects, but they can be passed also as a string.
        Actions, passed as an object but not created yet, will be created.
        If the specified event is not assigned to the policy, it will be assigned.

        Args:
            event: Name of the event under which the actions will be assigned.
            actions: If :py:class:`list` (or similar), all of these actions will be set under
                TRUE section. If :py:class:`dict`, the action is key and value specifies its
                placement. If it's True, then it will be put in the TRUE section and so on.
        """
        true_actions, false_actions = [], []
        if isinstance(actions, Action):
            true_actions.append(actions)
        elif isinstance(actions, list) or isinstance(actions, tuple) or isinstance(actions, set):
            true_actions.extend(actions)
        elif isinstance(actions, dict):
            for action, is_true in actions.iteritems():
                if is_true:
                    true_actions.append(action)
                else:
                    false_actions.append(action)
        else:
            raise TypeError("assign_actions_to_event expects, list, tuple, set or dict!")
        # Check whether actions exist
        for action in true_actions + false_actions:
            if isinstance(action, Action):
                if not action.exists:
                    action.create()
                    assert action.exists, "Could not create action {}!".format(action.description)
            else:  # string
                if not Action(action, "Tag").exists:
                    raise NameError("Action with name {} does not exist!".format(action))
        # Check whether we have all necessary events assigned
        if not self.is_event_assigned(event):
            self.assign_events(event, extend=True)
            assert self.is_event_assigned(event), "Could not assign event {}!".format(event)
        # And now we can assign actions
        self.testing_event = event
        view = navigate_to(self, "Event Details")
        assert view.is_displayed
        view.toolbar.configuration.item_select("Edit Actions for this Policy Event")
        view = self.create_view(EditEventView)
        assert view.is_displayed
        changed = view.fill({
            "true_actions": [str(action) for action in true_actions],
            "false_actions": [str(action) for action in false_actions]
        })
        if changed:
            view.save_button.click()
        else:
            view.cancel_button.click()
        view.flash.assert_success_message('Actions for Policy Event "{}" were saved'.format(
            event))

    @property
    def exists(self):
        policies = self.appliance.db.client["miq_policies"]
        return self.appliance.db.client.session\
            .query(policies.description)\
            .filter(policies.description == self.description)\
            .count() > 0

    @property
    def assigned_events(self):
        policies = self.appliance.db.client["miq_policies"]
        events = self.appliance.db.client["miq_event_definitions"]
        policy_contents = self.appliance.db.client["miq_policy_contents"]
        session = self.appliance.db.client.session
        policy_id = session.query(policies.id).filter(policies.description == self.description)
        assigned_events = session.query(policy_contents.miq_event_definition_id).filter(
            policy_contents.miq_policy_id == policy_id)
        return [event_name[0] for event_name in session.query(events.description).filter(
            events.id.in_(assigned_events))]


@navigator.register(PolicyCollection, "All")
class PolicyAll(CFMENavigateStep):
    VIEW = PoliciesAllView
    prerequisite = NavigateToAttribute("appliance.server", "ControlExplorer")

    def step(self):
        self.prerequisite_view.policies.tree.click_path("All Policies")


@navigator.register(BasePolicy, "Add")
class PolicyNew(CFMENavigateStep):
    VIEW = NewPolicyView
    prerequisite = NavigateToAttribute("collection", "All")

    def step(self):
        self.prerequisite_view.policies.tree.click_path(
            "All Policies",
            "{} Policies".format(self.obj.TYPE),
            "{} {} Policies".format(self.obj.TREE_NODE, self.obj.TYPE)
        )
        self.prerequisite_view.configuration.item_select("Add a New {} {} Policy".format(
            self.obj.PRETTY, self.obj.TYPE))


@navigator.register(BasePolicy, "Edit")
class PolicyEdit(CFMENavigateStep):
    VIEW = EditPolicyView
    prerequisite = NavigateToSibling("Details")

    def step(self):
        self.prerequisite_view.configuration.item_select("Edit Basic Info, Scope, and Notes")


@navigator.register(BasePolicy, "Details")
class PolicyDetails(CFMENavigateStep):
    VIEW = PolicyDetailsView
    prerequisite = NavigateToAttribute("collection", "All")

    def step(self):
        self.prerequisite_view.policies.tree.click_path(
            "All Policies",
            "{} Policies".format(self.obj.TYPE),
            "{} {} Policies".format(self.obj.TREE_NODE, self.obj.TYPE),
            self.obj.description
        )


@navigator.register(BasePolicy, "Condition Details")
class PolicyConditionDetails(CFMENavigateStep):
    VIEW = ConditionDetailsView
    prerequisite = NavigateToAttribute("appliance.server", "ControlExplorer")

    def step(self):
        self.view.policies.tree.click_path(
            "All Policies",
            "{} Policies".format(self.obj.TYPE),
            "{} {} Policies".format(self.obj.TREE_NODE, self.obj.TYPE),
            self.obj.description,
            self.obj.testing_condition.description
        )


@navigator.register(BasePolicy, "Event Details")
class PolicyEventDetails(CFMENavigateStep):
    VIEW = EventDetailsView
    prerequisite = NavigateToAttribute("appliance.server", "ControlExplorer")

    def step(self):
        self.view.policies.tree.click_path(
            "All Policies",
            "{} Policies".format(self.obj.TYPE),
            "{} {} Policies".format(self.obj.TREE_NODE, self.obj.TYPE),
            self.obj.description,
            self.obj.testing_event
        )


class HostCompliancePolicy(BasePolicy):

    TYPE = "Compliance"
    TREE_NODE = "Host"
    PRETTY = "Host / Node"


class VMCompliancePolicy(BasePolicy):

    TYPE = "Compliance"
    TREE_NODE = "Vm"
    PRETTY = "VM and Instance"


class ReplicatorCompliancePolicy(BasePolicy):

    TYPE = "Compliance"
    TREE_NODE = "Replicator"
    PRETTY = "Replicator"


class PodCompliancePolicy(BasePolicy):

    TYPE = "Compliance"
    TREE_NODE = "Pod"
    PRETTY = "Pod"


class ContainerNodeCompliancePolicy(BasePolicy):

    TYPE = "Compliance"
    TREE_NODE = "Container Node"
    PRETTY = "Node"


class ContainerImageCompliancePolicy(BasePolicy):

    TYPE = "Compliance"
    TREE_NODE = "Container Image"
    PRETTY = "Container Image"


class HostControlPolicy(BasePolicy):

    TYPE = "Control"
    TREE_NODE = "Host"
    PRETTY = "Host / Node"


class VMControlPolicy(BasePolicy):

    TYPE = "Control"
    TREE_NODE = "Vm"
    PRETTY = "VM and Instance"


class ReplicatorControlPolicy(BasePolicy):

    TYPE = "Control"
    TREE_NODE = "Replicator"
    PRETTY = "Replicator"


class PodControlPolicy(BasePolicy):

    TYPE = "Control"
    TREE_NODE = "Pod"
    PRETTY = "Pod"


class ContainerNodeControlPolicy(BasePolicy):

    TYPE = "Control"
    TREE_NODE = "Container Node"
    PRETTY = "Node"


class ContainerImageControlPolicy(BasePolicy):

    TYPE = "Control"
    TREE_NODE = "Container Image"
    PRETTY = "Container Image"
