var _jobs = undefined;

define([
  "util"
], function(util) {
  'use strict';

  /*
  * job system design:
   *
   * all jobs have tags.
   * only one job with a given tag can run at a time.
   *
  * */

  var exports = _jobs = {};

  var JobFlags = {
  };

  var JobStatus = exports.JobStatus = class JobStatus {
    constructor() {
      this.percent = 0.0;
    }
  }

  var Job = exports.Job = class Job {
    constructor(iter, tag, owner) {
      this.iter = iter;
      this.tag = tag;
      this.owner = owner;
      this.dead = false;
      this.status = new JobStatus();

      this.thens = [];
      this.catcher = undefined;
    }

    then(cb) {
      this.thens.push(cb);
    }

    catch(cb) {
      this.catcher = cb;
    }

    stop() {
      this.dead = true;
    }

    next() {
      if (this.dead) {
        return this.dead;
      }

      var ret = this.iter.next();
      if (ret.done) {
        this.dead = {done: true, value : undefined};
      }

      return ret;
    }
  };

  var JobManager = exports.JobManager = class JobManager {
    constructor() {
      this.jobs = [];
      this.job_tagmap = {};
      this.thenqueue = [];
    }

    //only one job with a given tag can run at once
    //if a job with same tag is already running, it will be
    //stopped
    run(jobiter, tag, owner) {
      var job = new Job(jobiter, tag, owner);

      if (tag in this.job_tagmap) {
        this.job_tagmap[tag].stop();
        this.jobs.remove(this.job_tagmap[tag]);
      }


      this.job_tagmap[tag] = job;
      this.jobs.push(job);

      return job;
    }

    next() {
      for (var i=0; i<this.jobs.length; i++) {
        var job = this.jobs[i];
        var ret = job.next();

        if (ret.done) {
          delete this.job_tagmap[job.tag];
          this.jobs.pop_i(i);
          this.thenqueue.push(job);
          i--;
        }
      }

      for (var i=0; i<this.thenqueue.length; i++) {
        for (var then of this.thenqueue[i].thens) {
          try {
            then();
          } catch (error) {
            util.print_stack(error);
            console.log("Error while executing job promise callback");
          }
        }
      }

      this.thenqueue.length = 0;
    }
  };

  return exports;
});
