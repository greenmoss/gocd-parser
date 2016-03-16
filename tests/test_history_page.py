import os
import mock

import gocd_parser.handler.history
import gocd_parser.retriever.server

from gocd_parser.retriever import url

class TestHistoryPager:
    @mock.patch('gocd_parser.retriever.url.URL')
    def test_passing(self, unused_mock):
        history_json = """
            {
              "pagination": {
                "offset": 0,
                "page_size": 10,
                "total": 1
              },
              "pipelines": [
                {
                  "build_cause": {
                    "approver": "",
                    "material_revisions": [
                      {
                        "changed": true,
                        "material": {
                          "description": "URL: https://some.org/some-org/some-pipeline, Branch: master",
                          "fingerprint": "afb72b26536242e1a474eec19e865b1e2e824fed5b52fa9016a0d4f7e0e76560",
                          "id": 36746,
                          "type": "Git"
                        },
                        "modifications": [
                          {
                            "comment": "Initial commit of repo",
                            "email_address": null,
                            "id": 189052,
                            "modified_time": 1456532246000,
                            "revision": "b1505c9f5b20fef7a31c648070ca2c75ee715d56",
                            "user_name": "Some Author <someone@some.org>"
                          }
                        ]
                      }
                    ],
                    "trigger_forced": false,
                    "trigger_message": "modified by Some Author <someone@some.org>"
                  },
                  "can_run": true,
                  "comment": null,
                  "counter": 1,
                  "id": 119009,
                  "label": "1",
                  "name": "some-pipeline",
                  "natural_order": 1.0,
                  "preparing_to_schedule": false,
                  "stages": [
                    {
                      "approval_type": "success",
                      "approved_by": "someone",
                      "can_run": true,
                      "counter": "2",
                      "id": 332522,
                      "jobs": [
                        {
                          "id": 405731,
                          "name": "defaultJob",
                          "result": "Passed",
                          "scheduled_date": 1456532862025,
                          "state": "Completed"
                        }
                      ],
                      "name": "defaultStage",
                      "operate_permission": true,
                      "rerun_of_counter": null,
                      "result": "Passed",
                      "scheduled": true
                    }
                  ]
                }
              ]
            }
        """
        # this mock should be improved; see
        # https://stackoverflow.com/questions/35999499
        g = gocd_parser.retriever.server.Server('http://localhost:8080/go')
        retrieved = url.URL(g, 'foo')
        retrieved.contents.__getitem__.return_value = history_json
        p = gocd_parser.handler.history.HistoryPager(g, 'ignored')
        assert p.pages[0].first['name'] == 'some-pipeline'
        assert p.pages[0].passing is True
        assert p.pages[0].last_completed['counter'] == 1
        assert p.pages[0].last_passing['counter'] == 1
        assert p.pages[0].first_of_current_failures is None
        assert p.pages[0].failure_duration is None

    @mock.patch('gocd_parser.retriever.url.URL')
    def test_one_passing_two_failed(self, unused_mock):
        history_json = """
        {
          "pagination": {
            "offset": 0,
            "page_size": 10,
            "total": 3
          },
          "pipelines": [
            {
              "build_cause": {
                "approver": "anonymous",
                "material_revisions": [
                  {
                    "changed": false,
                    "material": {
                      "description": "UserAcceptance",
                      "fingerprint": "eef662f23116e3b49e932b34e9bbbf10ffe727ef6b61d55a51f84ae3a469f613",
                      "id": 3,
                      "type": "Pipeline"
                    },
                    "modifications": [
                      {
                        "comment": "Unknown",
                        "email_address": null,
                        "id": 4,
                        "modified_time": 1458082828318,
                        "revision": "UserAcceptance/1/Approved/1",
                        "user_name": "Unknown"
                      }
                    ]
                  },
                  {
                    "changed": false,
                    "material": {
                      "description": "FunctionalTests",
                      "fingerprint": "f3dec0cc10fd6f4c182ca8cde67dd50924d8e5096e94407071422a0be7a211bf",
                      "id": 2,
                      "type": "Pipeline"
                    },
                    "modifications": [
                      {
                        "comment": "Unknown",
                        "email_address": null,
                        "id": 3,
                        "modified_time": 1458082651355,
                        "revision": "FunctionalTests/1/functionalTests/1",
                        "user_name": "Unknown"
                      }
                    ]
                  }
                ],
                "trigger_forced": true,
                "trigger_message": "Forced by anonymous"
              },
              "can_run": true,
              "comment": null,
              "counter": 3,
              "id": 9,
              "label": "3",
              "name": "DeployStaging",
              "natural_order": 3.0,
              "preparing_to_schedule": false,
              "stages": [
                {
                  "approval_type": "success",
                  "approved_by": "anonymous",
                  "can_run": true,
                  "counter": "1",
                  "id": 25,
                  "jobs": [
                    {
                      "id": 28,
                      "name": "DeployApplication",
                      "result": "Failed",
                      "scheduled_date": 1458150075524,
                      "state": "Completed"
                    }
                  ],
                  "name": "Deploy",
                  "operate_permission": true,
                  "rerun_of_counter": null,
                  "result": "Failed",
                  "scheduled": true
                },
                {
                  "approval_type": null,
                  "approved_by": null,
                  "can_run": true,
                  "counter": "1",
                  "id": 0,
                  "jobs": [],
                  "name": "Verify",
                  "operate_permission": true,
                  "rerun_of_counter": null,
                  "scheduled": false
                }
              ]
            },
            {
              "build_cause": {
                "approver": "anonymous",
                "material_revisions": [
                  {
                    "changed": false,
                    "material": {
                      "description": "UserAcceptance",
                      "fingerprint": "eef662f23116e3b49e932b34e9bbbf10ffe727ef6b61d55a51f84ae3a469f613",
                      "id": 3,
                      "type": "Pipeline"
                    },
                    "modifications": [
                      {
                        "comment": "Unknown",
                        "email_address": null,
                        "id": 4,
                        "modified_time": 1458082828318,
                        "revision": "UserAcceptance/1/Approved/1",
                        "user_name": "Unknown"
                      }
                    ]
                  },
                  {
                    "changed": false,
                    "material": {
                      "description": "FunctionalTests",
                      "fingerprint": "f3dec0cc10fd6f4c182ca8cde67dd50924d8e5096e94407071422a0be7a211bf",
                      "id": 2,
                      "type": "Pipeline"
                    },
                    "modifications": [
                      {
                        "comment": "Unknown",
                        "email_address": null,
                        "id": 3,
                        "modified_time": 1458082651355,
                        "revision": "FunctionalTests/1/functionalTests/1",
                        "user_name": "Unknown"
                      }
                    ]
                  }
                ],
                "trigger_forced": true,
                "trigger_message": "Forced by anonymous"
              },
              "can_run": true,
              "comment": null,
              "counter": 2,
              "id": 8,
              "label": "2",
              "name": "DeployStaging",
              "natural_order": 2.0,
              "preparing_to_schedule": false,
              "stages": [
                {
                  "approval_type": "success",
                  "approved_by": "anonymous",
                  "can_run": true,
                  "counter": "1",
                  "id": 24,
                  "jobs": [
                    {
                      "id": 27,
                      "name": "DeployApplication",
                      "result": "Failed",
                      "scheduled_date": 1458149992471,
                      "state": "Completed"
                    }
                  ],
                  "name": "Deploy",
                  "operate_permission": true,
                  "rerun_of_counter": null,
                  "result": "Failed",
                  "scheduled": true
                },
                {
                  "approval_type": null,
                  "approved_by": null,
                  "can_run": true,
                  "counter": "1",
                  "id": 0,
                  "jobs": [],
                  "name": "Verify",
                  "operate_permission": true,
                  "rerun_of_counter": null,
                  "scheduled": false
                }
              ]
            },
            {
              "build_cause": {
                "approver": "",
                "material_revisions": [
                  {
                    "changed": true,
                    "material": {
                      "description": "UserAcceptance",
                      "fingerprint": "eef662f23116e3b49e932b34e9bbbf10ffe727ef6b61d55a51f84ae3a469f613",
                      "id": 3,
                      "type": "Pipeline"
                    },
                    "modifications": [
                      {
                        "comment": "Unknown",
                        "email_address": null,
                        "id": 4,
                        "modified_time": 1458082828318,
                        "revision": "UserAcceptance/1/Approved/1",
                        "user_name": "Unknown"
                      }
                    ]
                  },
                  {
                    "changed": true,
                    "material": {
                      "description": "FunctionalTests",
                      "fingerprint": "f3dec0cc10fd6f4c182ca8cde67dd50924d8e5096e94407071422a0be7a211bf",
                      "id": 2,
                      "type": "Pipeline"
                    },
                    "modifications": [
                      {
                        "comment": "Unknown",
                        "email_address": null,
                        "id": 3,
                        "modified_time": 1458082651355,
                        "revision": "FunctionalTests/1/functionalTests/1",
                        "user_name": "Unknown"
                      }
                    ]
                  }
                ],
                "trigger_forced": false,
                "trigger_message": "triggered by UserAcceptance/1/Approved/1"
              },
              "can_run": true,
              "comment": null,
              "counter": 1,
              "id": 5,
              "label": "1",
              "name": "DeployStaging",
              "natural_order": 1.0,
              "preparing_to_schedule": false,
              "stages": [
                {
                  "approval_type": "success",
                  "approved_by": "anonymous",
                  "can_run": true,
                  "counter": "3",
                  "id": 20,
                  "jobs": [
                    {
                      "id": 23,
                      "name": "DeployApplication",
                      "result": "Passed",
                      "scheduled_date": 1458149880141,
                      "state": "Completed"
                    }
                  ],
                  "name": "Deploy",
                  "operate_permission": true,
                  "rerun_of_counter": null,
                  "result": "Passed",
                  "scheduled": true
                },
                {
                  "approval_type": "success",
                  "approved_by": "changes",
                  "can_run": true,
                  "counter": "2",
                  "id": 21,
                  "jobs": [
                    {
                      "id": 24,
                      "name": "verify",
                      "result": "Passed",
                      "scheduled_date": 1458149894107,
                      "state": "Completed"
                    }
                  ],
                  "name": "Verify",
                  "operate_permission": true,
                  "rerun_of_counter": null,
                  "result": "Passed",
                  "scheduled": true
                }
              ]
            }
          ]
        }
        """
        # this mock should be improved; see
        # https://stackoverflow.com/questions/35999499
        g = gocd_parser.retriever.server.Server('http://localhost:8080/go')
        retrieved = url.URL(g, 'foo')
        retrieved.contents.__getitem__.return_value = history_json
        p = gocd_parser.handler.history.HistoryPager(g, 'ignored')
        assert p.pages[0].passing is False
        assert p.pages[0].last_completed['counter'] == 3
        assert p.pages[0].last_passing['counter'] == 1
        assert p.pages[0].first_of_current_failures is not None
        assert p.pages[0].first_of_current_failures['counter'] == 2
        assert p.pages[0].failure_duration is not None
