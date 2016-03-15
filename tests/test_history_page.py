import os
import mock

import gocd_parser.handler.history
import gocd_parser.retriever.server

from gocd_parser.retriever import url

class TestHistoryPager:
    @mock.patch('gocd_parser.retriever.url.URL')
    def test_one(self, unused_mock):
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
